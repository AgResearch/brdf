--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY labresourcefact
    ADD CONSTRAINT "$1" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


