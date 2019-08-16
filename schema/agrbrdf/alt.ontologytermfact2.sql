--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologytermfact2
    ADD CONSTRAINT "$1" FOREIGN KEY (ontologytermid) REFERENCES ontologytermfact(obid);


