--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplelistmembershiplink
    ADD CONSTRAINT "$1" FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplelistmembershiplink
    ADD CONSTRAINT "$2" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


