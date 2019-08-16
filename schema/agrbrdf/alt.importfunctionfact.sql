--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY importfunctionfact
    ADD CONSTRAINT "$1" FOREIGN KEY (importfunction) REFERENCES importfunction(obid);


