--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcelistmembershiplink
    ADD CONSTRAINT "$1" FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcelistmembershiplink
    ADD CONSTRAINT "$2" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


